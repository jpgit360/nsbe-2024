// app/api/auth/[auth0]/route.js
import { handleAuth } from '@auth0/nextjs-auth0';

console.log('the AUTH0_SECRET env var is set: ', !!process.env.AUTH0_SECRET);
export const GET = handleAuth();