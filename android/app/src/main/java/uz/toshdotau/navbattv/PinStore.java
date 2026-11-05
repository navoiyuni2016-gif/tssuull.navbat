package uz.toshdotau.navbattv;
import android.content.SharedPreferences;
import android.util.Base64;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.nio.charset.StandardCharsets;

final class PinStore {
    static void save(SharedPreferences prefs,String pin) {
        byte[] salt=new byte[24];new SecureRandom().nextBytes(salt);
        prefs.edit().putString("pin_salt",Base64.encodeToString(salt,Base64.NO_WRAP)).putString("pin_hash",digest(salt,pin)).apply();
    }
    static boolean matches(SharedPreferences prefs,String pin) {
        try {
            byte[] salt=Base64.decode(prefs.getString("pin_salt",""),Base64.NO_WRAP);
            return salt.length==24&&MessageDigest.isEqual(prefs.getString("pin_hash","").getBytes(StandardCharsets.US_ASCII),digest(salt,pin).getBytes(StandardCharsets.US_ASCII));
        }catch(Exception error){return false;}
    }
    private static String digest(byte[] salt,String pin) {
        try {MessageDigest d=MessageDigest.getInstance("SHA-256");d.update(salt);return Base64.encodeToString(d.digest(pin.getBytes(StandardCharsets.UTF_8)),Base64.NO_WRAP);}
        catch(Exception error){throw new IllegalStateException(error);}
    }
}
