package uz.toshdotau.navbattv;

import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import android.content.Context;
import android.view.View;
import android.view.WindowManager;
import java.net.*;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.Enumeration;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.*;

@RunWith(AndroidJUnit4.class)
public class TvActivityTest {
    @Test public void fullscreenStoredSettingsOfflineRecoveryAndAutomaticAudio() throws Exception {
        Context context=InstrumentationRegistry.getInstrumentation().getTargetContext();context.getSharedPreferences("tv",Context.MODE_PRIVATE).edit().clear().commit();
        String host=null;
        for(Enumeration<NetworkInterface> interfaces=NetworkInterface.getNetworkInterfaces();interfaces.hasMoreElements();) {
            for(Enumeration<InetAddress> addresses=interfaces.nextElement().getInetAddresses();addresses.hasMoreElements();) {
                InetAddress address=addresses.nextElement();if(address instanceof Inet4Address&&address.isSiteLocalAddress()){host=address.getHostAddress();break;}
            }
            if(host!=null)break;
        }
        assertNotNull("Emulator private IPv4 is required",host);
        int port;try(ServerSocket reservation=new ServerSocket(0)){port=reservation.getLocalPort();}
        String base="http://"+host+":"+port;
        try(ActivityScenario<MainActivity> scenario=ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity->{
                assertTrue((activity.getWindow().getAttributes().flags&WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)!=0);
                assertTrue(activity.web.getSettings().getJavaScriptEnabled());assertTrue(activity.web.getSettings().getDomStorageEnabled());
                assertFalse(activity.web.getSettings().getMediaPlaybackRequiresUserGesture());assertFalse(activity.web.getSettings().getAllowFileAccess());assertFalse(activity.web.getSettings().getAllowContentAccess());
                activity.saveConfiguration(base,"7432","7432",true);
                assertEquals(base,activity.prefs.getString("server",""));assertTrue(PinStore.matches(activity.prefs,"7432"));assertFalse(PinStore.matches(activity.prefs,"0000"));assertNotEquals("7432",activity.prefs.getString("pin_hash",""));
            });
            AtomicBoolean disconnected=new AtomicBoolean();
            for(int i=0;i<100;i++){scenario.onActivity(a->disconnected.set(a.disconnected&&a.connection.getVisibility()==View.VISIBLE));if(disconnected.get())break;Thread.sleep(100);}
            assertTrue("A failed LAN connection must show a reconnect state",disconnected.get());
            try(TinyServer server=new TinyServer(port)) {
                AtomicReference<String> title=new AtomicReference<>("");
                for(int i=0;i<200;i++){scenario.onActivity(a->title.set(a.web.getTitle()));if("AUDIO_OK".equals(title.get()))break;Thread.sleep(100);}
                assertEquals("Autoretry must recover and play audio without a tap","AUDIO_OK",title.get());
                scenario.onActivity(a->{assertFalse(a.disconnected);assertEquals(View.GONE,a.connection.getVisibility());});
            }
        }
    }
    private static final class TinyServer implements AutoCloseable {
        final ServerSocket socket;final Thread thread;volatile boolean closed=false;
        TinyServer(int port) throws IOException {
            socket=new ServerSocket();socket.setReuseAddress(true);socket.bind(new InetSocketAddress(port));
            thread=new Thread(()->{while(!closed){try(Socket client=socket.accept()){
                BufferedReader reader=new BufferedReader(new InputStreamReader(client.getInputStream(),StandardCharsets.US_ASCII));String first=reader.readLine();if(first==null)continue;String line;while((line=reader.readLine())!=null&&!line.isEmpty()){}
                boolean audio=first.contains("/tone.wav");byte[] body;
                if(audio){ByteBuffer wav=ByteBuffer.allocate(1644).order(ByteOrder.LITTLE_ENDIAN);wav.put("RIFF".getBytes(StandardCharsets.US_ASCII));wav.putInt(1636);wav.put("WAVEfmt ".getBytes(StandardCharsets.US_ASCII));wav.putInt(16);wav.putShort((short)1);wav.putShort((short)1);wav.putInt(8000);wav.putInt(16000);wav.putShort((short)2);wav.putShort((short)16);wav.put("data".getBytes(StandardCharsets.US_ASCII));wav.putInt(1600);body=wav.array();}
                else body=("<!doctype html><meta name='viewport' content='width=device-width'><title>TV_CONNECTING</title><script>new Audio('/tone.wav').play().then(function(){document.title='AUDIO_OK'}).catch(function(e){document.title='AUDIO_FAILED:'+e.name})</script>").getBytes(StandardCharsets.UTF_8);
                OutputStream out=client.getOutputStream();out.write(("HTTP/1.1 200 OK\r\nContent-Type: "+(audio?"audio/wav":"text/html; charset=utf-8")+"\r\nContent-Length: "+body.length+"\r\nConnection: close\r\n\r\n").getBytes(StandardCharsets.US_ASCII));out.write(body);out.flush();
            }catch(IOException error){if(!closed)throw new RuntimeException(error);}}},"test-tv-server");thread.start();
        }
        @Override public void close() throws Exception{closed=true;socket.close();thread.join(2000);}
    }
}
