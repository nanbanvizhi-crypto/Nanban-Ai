package com.nanban.app;

import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.text.InputType;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;

import androidx.appcompat.app.AppCompatActivity;

/**
 * Nanban Android — a thin WebView wrapper that opens the user's own Nanban server.
 *
 * On first launch, asks for the server URL (e.g. http://192.168.1.4:7860 for LAN,
 * or the Cloudflare Tunnel URL for internet access). Stores it in SharedPreferences
 * so subsequent launches go straight to the app. Menu has "Change server URL".
 */
public class MainActivity extends AppCompatActivity {
    private static final String PREFS = "nanban_prefs";
    private static final String KEY_URL = "server_url";

    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        web = findViewById(R.id.webview);

        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.getSettings().setDatabaseEnabled(true);
        web.getSettings().setCacheMode(android.webkit.WebSettings.LOAD_DEFAULT);
        web.getSettings().setMediaPlaybackRequiresUserGesture(false);
        web.getSettings().setMixedContentMode(android.webkit.WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        web.getSettings().setAllowFileAccess(true);
        web.getSettings().setLoadWithOverviewMode(true);
        web.getSettings().setUseWideViewPort(true);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                // Stay inside the webview for same-host links; farm external links out to the browser.
                Uri uri = req.getUrl();
                String current = view.getUrl();
                if (current != null && uri != null && uri.getHost() != null
                        && Uri.parse(current).getHost() != null
                        && uri.getHost().equals(Uri.parse(current).getHost())) {
                    return false;
                }
                startActivity(new android.content.Intent(android.content.Intent.ACTION_VIEW, uri));
                return true;
            }
        });
        web.setWebChromeClient(new WebChromeClient());

        String url = getStoredUrl();
        if (url == null || url.isEmpty()) {
            promptForUrl(true);
        } else {
            web.loadUrl(url);
        }
    }

    private String getStoredUrl() {
        SharedPreferences p = getSharedPreferences(PREFS, MODE_PRIVATE);
        return p.getString(KEY_URL, "");
    }

    private void storeUrl(String url) {
        getSharedPreferences(PREFS, MODE_PRIVATE).edit().putString(KEY_URL, url).apply();
    }

    private void promptForUrl(final boolean isFirstRun) {
        final EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        input.setHint("http://192.168.1.4:7860");
        input.setText(getStoredUrl());

        new AlertDialog.Builder(this)
            .setTitle(isFirstRun ? "Enter your Nanban server URL" : "Change server URL")
            .setMessage("Example: http://192.168.1.4:7860 (LAN) or https://your-tunnel.trycloudflare.com")
            .setView(input)
            .setPositiveButton("Connect", (dialog, which) -> {
                String url = input.getText().toString().trim();
                if (!url.startsWith("http://") && !url.startsWith("https://")) {
                    url = "http://" + url;
                }
                storeUrl(url);
                web.loadUrl(url);
            })
            .setCancelable(!isFirstRun)
            .show();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        menu.add(0, 1, 0, "Reload");
        menu.add(0, 2, 0, "Change server URL");
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == 1) { web.reload(); return true; }
        if (item.getItemId() == 2) { promptForUrl(false); return true; }
        return super.onOptionsItemSelected(item);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && web.canGoBack()) {
            web.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
}
