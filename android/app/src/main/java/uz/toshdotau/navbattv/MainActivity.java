package uz.toshdotau.navbattv;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkRequest;
import android.net.http.SslError;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.provider.Settings;
import android.text.InputType;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.WindowManager;
import android.webkit.SslErrorHandler;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import java.io.ByteArrayInputStream;

public class MainActivity extends Activity {
    WebView web;
    TextView connection;
    SharedPreferences prefs;
    String server="";
    boolean disconnected=false,mainError=false,active=false;
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final Runnable retry=()->loadTV();
    private ConnectivityManager connectivity;
    private ConnectivityManager.NetworkCallback networkCallback;
    private AlertDialog settingsDialog,pinDialog;
    private int failures=0;
    private long blockedUntil=0;

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        prefs=getSharedPreferences("tv",MODE_PRIVATE);server=prefs.getString("server","");
        FrameLayout root=new FrameLayout(this);root.setBackgroundColor(Color.rgb(16,45,84));
        web=new WebView(this);root.addView(web,new FrameLayout.LayoutParams(-1,-1));
        connection=new TextView(this);connection.setTextColor(Color.WHITE);connection.setBackgroundColor(0xEE102D54);connection.setTextSize(20);connection.setPadding(24,18,24,18);connection.setGravity(Gravity.CENTER);
        FrameLayout.LayoutParams banner=new FrameLayout.LayoutParams(-1,-2,Gravity.BOTTOM);root.addView(connection,banner);connection.setVisibility(View.GONE);
        setContentView(root);fullscreen();
        WebSettings settings=web.getSettings();settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);
        settings.setUseWideViewPort(true);settings.setLoadWithOverviewMode(true);settings.setTextZoom(100);
        settings.setMediaPlaybackRequiresUserGesture(false);settings.setAllowFileAccess(false);settings.setAllowContentAccess(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);settings.setSupportMultipleWindows(false);settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){return !UrlPolicy.navigationAllowed(server,request.getUrl().toString());}
            @Override public boolean shouldOverrideUrlLoading(WebView view,String url){return !UrlPolicy.navigationAllowed(server,url);}
            @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request) {
                if(UrlPolicy.sameOrigin(server,request.getUrl().toString()))return null;
                return new WebResourceResponse("text/plain","UTF-8",new ByteArrayInputStream(new byte[0]));
            }
            @Override public void onPageStarted(WebView view,String url,android.graphics.Bitmap icon){mainError=false;}
            @Override public void onPageFinished(WebView view,String url) {
                if(!mainError&&UrlPolicy.navigationAllowed(server,url)) {
                    disconnected=false;connection.setVisibility(View.GONE);handler.removeCallbacks(retry);
                    view.evaluateJavascript("(function(){try{new Function('return ({x:1})?.x');return true}catch(e){return false}})()",value->{
                        if("false".equals(value)){connection.setText("Android System WebView eskirgan. Uni yangilang.");connection.setVisibility(View.VISIBLE);}
                    });
                }
            }
            @Override public void onReceivedError(WebView view,WebResourceRequest request,WebResourceError error){if(request.isForMainFrame())showDisconnected();}
            @Override public void onReceivedError(WebView view,int code,String description,String url){if(url.equals(server+"/tv?autostart=1"))showDisconnected();}
            @Override public void onReceivedHttpError(WebView view,WebResourceRequest request,WebResourceResponse response){if(request.isForMainFrame())showDisconnected();}
            @Override public void onReceivedSslError(WebView view,SslErrorHandler error,SslError ssl){error.cancel();showDisconnected();}
        });
        connectivity=(ConnectivityManager)getSystemService(Context.CONNECTIVITY_SERVICE);
        networkCallback=new ConnectivityManager.NetworkCallback(){@Override public void onAvailable(Network network){handler.post(()->{if(active&&disconnected)loadTV();});}};
        try {connectivity.registerNetworkCallback(new NetworkRequest.Builder().build(),networkCallback);}catch(RuntimeException ignored){}
        if(server.isEmpty())showSettings();else loadTV();
    }
    private void fullscreen(){getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY|View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN|View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_LAYOUT_STABLE);}
    @Override public void onWindowFocusChanged(boolean focus){super.onWindowFocusChanged(focus);if(focus)fullscreen();}
    @Override public void onResume(){super.onResume();active=true;web.onResume();fullscreen();if(disconnected)handler.post(retry);}
    @Override public void onPause(){active=false;handler.removeCallbacks(retry);web.onPause();super.onPause();}
    @Override public void onDestroy(){handler.removeCallbacksAndMessages(null);try{connectivity.unregisterNetworkCallback(networkCallback);}catch(RuntimeException ignored){}web.destroy();super.onDestroy();}
    void loadTV(){
        handler.removeCallbacks(retry);
        if(server.isEmpty())return;
        web.loadUrl(server+"/tv?autostart=1");
    }
    void showDisconnected(){
        mainError=true;disconnected=true;connection.setText("Serverga ulanmoqda… Tarmoq va serverni tekşiring.");connection.setVisibility(View.VISIBLE);
        handler.removeCallbacks(retry);if(active)handler.postDelayed(retry,5000);
    }
    @Override public boolean onKeyDown(int code,KeyEvent event){if(code==KeyEvent.KEYCODE_MENU&&event.getRepeatCount()==0){authenticate();return true;}return super.onKeyDown(code,event);}
    @Override public void onBackPressed(){authenticate();}
    private LinearLayout form(){LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);int pad=(int)(20*getResources().getDisplayMetrics().density);box.setPadding(pad,pad,pad,pad);return box;}
    private EditText input(LinearLayout box,String hint,String value,boolean password){EditText field=new EditText(this);field.setHint(hint);field.setSingleLine(true);field.setText(value);field.setInputType(password?InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_VARIATION_PASSWORD:InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_URI);box.addView(field,new LinearLayout.LayoutParams(-1,-2));return field;}
    void saveConfiguration(String address,String pin,String confirmation,boolean autostart){
        String normalized=UrlPolicy.normalize(address);
        if(!pin.isEmpty()){
            if(!pin.matches("[0-9]{4,8}"))throw new IllegalArgumentException("PIN 4–8 raqamdan iborat bölsin.");
            if(!pin.equals(confirmation))throw new IllegalArgumentException("PINlar bir xil emas.");
            PinStore.save(prefs,pin);
        }else if(!prefs.contains("pin_hash"))throw new IllegalArgumentException("Sozlamalar uçun PIN kiriting.");
        prefs.edit().putString("server",normalized).putBoolean("autostart",autostart).apply();server=normalized;loadTV();
    }
    void showSettings(){
        if(settingsDialog!=null&&settingsDialog.isShowing())return;
        LinearLayout box=form();TextView info=new TextView(this);info.setText("Server kompyuteri va X96 bir lokal tarmoqda bölsin.\n127.0.0.1 emas, kompyuterning lokal IP manzilini yozing.");box.addView(info);
        EditText address=input(box,"Masalan: 192.168.1.10:8080",server,false);
        EditText pin=input(box,prefs.contains("pin_hash")?"Yangi PIN (özgartirmaslik uçun böş qoldiring)":"Sozlamalar PINi (4–8 raqam)","",true);
        EditText confirm=input(box,"PINni takrorlang","",true);
        CheckBox boot=new CheckBox(this);boot.setText("Box yoqilganda avtomatik oçiş");boot.setChecked(prefs.getBoolean("autostart",true));box.addView(boot);
        TextView instructions=new TextView(this);instructions.setText("Android 10+ da avtostart uçun ilovani Home/Launcher sifatida tanlang. Sozlamalar: pultda MENU yoki BACK → PIN.");box.addView(instructions);
        settingsDialog=new AlertDialog.Builder(this).setTitle("TOŞDÖTAU TV — sozlamalar").setView(box).setPositiveButton("Saqlaş",null).setNegativeButton(server.isEmpty()?"Çiqiş":"Yopiş",(dialog,which)->{if(server.isEmpty())finish();}).setNeutralButton("Android / Home sozlamalari",null).create();
        settingsDialog.setCancelable(!server.isEmpty());settingsDialog.show();
        settingsDialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{try{saveConfiguration(address.getText().toString(),pin.getText().toString(),confirm.getText().toString(),boot.isChecked());settingsDialog.dismiss();}catch(IllegalArgumentException error){address.setError(error.getMessage());}});
        settingsDialog.getButton(AlertDialog.BUTTON_NEUTRAL).setOnClickListener(v->{
            try{startActivity(new Intent(server.isEmpty()?Settings.ACTION_SETTINGS:Settings.ACTION_HOME_SETTINGS));}
            catch(RuntimeException error){try{startActivity(new Intent(Settings.ACTION_SETTINGS));}catch(RuntimeException ignored){Toast.makeText(this,"Android sozlamalarini tizim menyusidan oçing",Toast.LENGTH_LONG).show();}}
        });
    }
    private void authenticate(){
        if(server.isEmpty()){showSettings();return;}
        if(pinDialog!=null&&pinDialog.isShowing())return;
        if(SystemClock.elapsedRealtime()<blockedUntil){Toast.makeText(this,"30 soniya kuting",Toast.LENGTH_SHORT).show();return;}
        LinearLayout box=form();EditText value=input(box,"PIN","",true);
        pinDialog=new AlertDialog.Builder(this).setTitle("Sozlamalar PINi").setView(box).setPositiveButton("Kiriş",null).setNegativeButton("Bekor qiliş",null).create();pinDialog.show();
        pinDialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            if(PinStore.matches(prefs,value.getText().toString())){failures=0;pinDialog.dismiss();showSettings();}
            else{value.setText("");value.setError("PIN xato");if(++failures>=5){failures=0;blockedUntil=SystemClock.elapsedRealtime()+30000;pinDialog.dismiss();}}
        });
    }
}
