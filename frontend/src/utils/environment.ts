export const getBackendUrl = (): string => {
  // Prioritize the environment variable if it exists
  const envBackendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (envBackendUrl) {
    return envBackendUrl;
  }

  // For client-side, determine the URL based on hostname
  if (typeof window !== 'undefined') {
    // Check if running in production
    if (window.location.hostname.includes('a51mn.xyz')) {
      return 'https://api.a51mn.xyz';
    }
    
    // Check if using Docker local environment 
    return 'http://localhost:8080';
  }

  // Server-side rendering fallback
  return 'http://localhost:8080';
};