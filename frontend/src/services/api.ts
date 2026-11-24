import axios from "axios";
import { useAuthStore } from "../stores/authStore";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // Crucial for HttpOnly cookies (refresh tokens)
});

// Request Interceptor: Attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    console.log("[API Request Interceptor] Token in store:", token ? `${token.substring(0, 15)}...` : "NONE");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log("[API Request Interceptor] Attached Authorization header:", config.headers.Authorization.substring(0, 25) + "...");
    } else {
      console.warn("[API Request Interceptor] No token attached!");
    }
    return config;
  },
  (error) => {
    console.error("[API Request Interceptor] Error:", error);
    return Promise.reject(error);
  }
);

// Response Interceptor: Handle token expiration
api.interceptors.response.use(
  (response) => {
    console.log("[API Response Interceptor] Success response for:", response.config.url);
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    console.error("[API Response Interceptor] Error response status:", error.response?.status, "for url:", originalRequest?.url);
    
    // If token has expired, try to refresh (except for login/refresh requests)
    const isAuthRequest = originalRequest?.url?.includes("/auth/login") || originalRequest?.url?.includes("/auth/refresh");
    if (error.response?.status === 401 && !originalRequest._retry && !isAuthRequest) {
      originalRequest._retry = true;
      console.log("[API Response Interceptor] Attempting token refresh...");
      try {
        // Send request to refresh token (HttpOnly cookie will be automatically sent)
        const res = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL || "/api/v1"}/auth/refresh`,
          {},
          { withCredentials: true }
        );
        
        const newAccessToken = res.data.access_token;
        console.log("[API Response Interceptor] Token refreshed successfully. New token:", newAccessToken ? `${newAccessToken.substring(0, 15)}...` : "NONE");
        useAuthStore.getState().updateAccessToken(newAccessToken);
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        console.error("[API Response Interceptor] Refresh failed, logging out user...", refreshError);
        // Refresh token failed -> Force logout
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
