export const getBackendUrl = (): string => {
  // Use only the environment variable
  const envBackendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  
  // If it exists, use it (this will be embedded at build time by Next.js)
  if (envBackendUrl) {
    return envBackendUrl;
  }

  // Only for local development
  return 'http://localhost:8080';
};