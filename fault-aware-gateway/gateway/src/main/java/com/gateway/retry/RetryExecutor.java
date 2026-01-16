package com.gateway.retry;

import org.springframework.stereotype.Component;
import java.util.function.Supplier;

@Component
public class RetryExecutor {
    public String execute(Supplier<String> call) {
        int attempts = 0;

        while (attempts < 3) {
            try {
                return call.get();
            } catch (Exception e) {
                attempts++;
            }
        }

        throw new RuntimeException("RETRIES_EXHAUSTED");
    }
}