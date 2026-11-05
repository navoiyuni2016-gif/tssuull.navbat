package uz.toshdotau.navbattv;
import java.net.URI;
import java.util.Locale;

/** One configured private LAN origin; no arbitrary navigation or local file access. */
public final class UrlPolicy {
    private UrlPolicy() {}
    public static String normalize(String input) {
        try {
            String text=input.trim();
            if(!text.contains("://")) text="http://"+text;
            URI uri=new URI(text);
            String scheme=uri.getScheme().toLowerCase(Locale.ROOT), host=uri.getHost();
            if(!scheme.equals("http")&&!scheme.equals("https")) throw new Exception();
            if(host==null||uri.getUserInfo()!=null||uri.getQuery()!=null||uri.getFragment()!=null) throw new Exception();
            if(uri.getPath()!=null&&!uri.getPath().isEmpty()&&!uri.getPath().equals("/")) throw new Exception();
            String[] parts=host.split("\\.");
            if(parts.length!=4) throw new Exception();
            int[] ip=new int[4];
            for(int i=0;i<4;i++) { if(!parts[i].matches("[0-9]{1,3}"))throw new Exception(); ip[i]=Integer.parseInt(parts[i]); if(ip[i]>255)throw new Exception(); }
            if(!(ip[0]==10 || (ip[0]==192&&ip[1]==168) || (ip[0]==172&&ip[1]>=16&&ip[1]<=31))) throw new Exception();
            int port=uri.getPort()==-1?8080:uri.getPort();
            if(port<1||port>65535)throw new Exception();
            return scheme+"://"+ip[0]+"."+ip[1]+"."+ip[2]+"."+ip[3]+":"+port;
        } catch(Exception error) {
            throw new IllegalArgumentException("Lokal IP manzilini kiriting. Masalan: 192.168.1.10:8080");
        }
    }
    public static boolean sameOrigin(String base,String url) {
        try {
            URI a=new URI(base),b=new URI(url);
            int port=b.getPort()==-1?("https".equals(b.getScheme())?443:80):b.getPort();
            return b.getUserInfo()==null&&a.getScheme().equals(b.getScheme())&&a.getHost().equalsIgnoreCase(b.getHost())&&a.getPort()==port;
        } catch(Exception error){return false;}
    }
    public static boolean navigationAllowed(String base,String url) {
        if(!sameOrigin(base,url))return false;
        try {String path=new URI(url).getPath();return path.equals("/tv")||path.equals("/tv-audio");}
        catch(Exception error){return false;}
    }
}
