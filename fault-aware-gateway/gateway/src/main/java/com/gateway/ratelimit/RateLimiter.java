package com.gateway.ratelimit;

import org.springframework.stereotype.Component;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class RateLimiter {
    private final ConcurrentHashMap<String, Integer> counters = new ConcurrentHashMap<>();
    private static final int LIMIT = 5;

    public boolean allow(String userId) {
        counters.putIfAbsent(userId, 0);
        int count = counters.compute(userId, (k, v) -> v + 1);
        return count <= LIMIT;
    }
}