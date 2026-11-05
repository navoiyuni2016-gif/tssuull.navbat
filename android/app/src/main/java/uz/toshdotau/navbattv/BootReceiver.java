package uz.toshdotau.navbattv;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ResolveInfo;
import android.os.Build;

public final class BootReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context,Intent intent) {
        if(!Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction()))return;
        if(!context.getSharedPreferences("tv",Context.MODE_PRIVATE).getBoolean("autostart",true))return;
        Intent home=new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME);
        ResolveInfo resolved=context.getPackageManager().resolveActivity(home,0);
        boolean isHome=resolved!=null&&resolved.activityInfo!=null&&context.getPackageName().equals(resolved.activityInfo.packageName);
        // Newer Android permits boot activity launch only in applicable system/launcher cases.
        if(Build.VERSION.SDK_INT<29||isHome) {
            try {context.startActivity(new Intent(context,MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TOP));}
            catch(RuntimeException ignored) { /* OEM firmware can still block background launches. */ }
        }
    }
}
