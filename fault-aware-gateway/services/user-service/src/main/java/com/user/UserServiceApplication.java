package com.user;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;

@SpringBootApplication
@RestController
public class UserServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);
    }

    @GetMapping("/users/{id}")
    public String getUser(@PathVariable("id") String id) throws InterruptedException {

        Thread.sleep((long) (Math.random() * 300));

        if (Math.random() < 0.2) {
            throw new RuntimeException("USER_SERVICE_FAILURE");
        }

        return "{ \"id\": \"" + id + "\" }";
    }
}