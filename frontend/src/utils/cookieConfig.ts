export interface CookieOptions {
  expires: number;
  secure: boolean;
  sameSite: 'strict' | 'lax' | 'none';
  path: string;
  domain?: string;
}

export const getCookieOptions = (isDev: boolean): CookieOptions => ({
  expires: 365,
  secure: !isDev,
  sameSite: 'strict',
  path: '/',
  domain: isDev ? undefined : process.env.NEXT_PUBLIC_COOKIE_DOMAIN
});