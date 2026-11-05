package uz.toshdotau.navbattv;
import org.junit.Test;
import static org.junit.Assert.*;
public class UrlPolicyTest {
    @Test public void normalizesPrivateAddresses(){assertEquals("http://192.168.1.10:8080",UrlPolicy.normalize("192.168.1.10"));assertEquals("http://10.0.2.15:1234",UrlPolicy.normalize("http://10.0.2.15:1234/"));assertEquals("https://172.16.1.4:8080",UrlPolicy.normalize("https://172.16.1.4"));}
    @Test public void rejectsPublicLoopbackCredentialsAndPaths(){for(String value:new String[]{"127.0.0.1","0.0.0.0","8.8.8.8","172.32.1.1","192.168.1.999","http://u:p@192.168.1.10","file:///etc/passwd","http://192.168.1.10/admin","http://192.168.1.10#x","http://192.168.1.10:65536"}){try{UrlPolicy.normalize(value);fail(value);}catch(IllegalArgumentException expected){}}}
    @Test public void restrictsNavigationAndResourceOrigins(){String base="http://192.168.1.10:8080";assertTrue(UrlPolicy.navigationAllowed(base,base+"/tv?autostart=1"));assertFalse(UrlPolicy.navigationAllowed(base,base+"/admin"));assertFalse(UrlPolicy.navigationAllowed(base,"http://192.168.1.11:8080/tv"));assertTrue(UrlPolicy.sameOrigin(base,base+"/audio/abc"));assertFalse(UrlPolicy.sameOrigin(base,"file:///data/x"));assertFalse(UrlPolicy.sameOrigin(base,"http://192.168.1.10/tv"));}
}
