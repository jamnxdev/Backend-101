package com.gateway.auth;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.springframework.stereotype.Component;
import java.io.IOException;

@Component
public class JwtAuthFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) req;
        HttpServletResponse response = (HttpServletResponse) res;

        String auth = request.getHeader("Authorization");

        if (auth == null || !auth.equals("Bearer valid-token")) {
            response.setStatus(401);
            response.getWriter().write("AUTH_INVALID");
            return;
        }

        request.setAttribute("user_id", "user-1");
        chain.doFilter(req, res);
    }
}