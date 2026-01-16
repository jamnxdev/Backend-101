package com.gateway.controller;

import com.gateway.cache.InMemoryCache;
import com.gateway.ratelimit.RateLimiter;
import com.gateway.retry.RetryExecutor;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.*;

import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

@RestController
public class GatewayController {
    
    private final RateLimiter rateLimiter;
    private final InMemoryCache cache;
    private final RetryExecutor retry;

    public GatewayController(RateLimiter rateLimiter, InMemoryCache cache, RetryExecutor retry) {
        this.rateLimiter = rateLimiter;
        this.cache = cache;
        this.retry = retry;
    }

    @GetMapping("/proxy/users/{id}")
    public String proxyUser(@PathVariable("id") String id, HttpServletRequest req) {
        String userId = (String) req.getAttribute("user_id");

        if (!rateLimiter.allow(userId)) {
            throw new RuntimeException("RATE_LIMIT_EXCEEDED");
        }
        String cached = cache.get(id);
        if (cached != null) {
            return cached;
        }
    
        String response = retry.execute(() -> {
            try {
                URL url = new URL("http://localhost:8081/users/" + id);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();

                conn.setRequestMethod("GET");

                Scanner sc = new Scanner(conn.getInputStream());
                return sc.useDelimiter("\\A").next();
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });

        cache.put(id, response);
        return response;
    }
}

