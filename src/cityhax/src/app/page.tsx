import Image from "next/image";
import { UserProvider } from "@auth0/nextjs-auth0/client";
import React from 'react';
import Link from 'next/link';

import { Outfit } from 'next/font/google';
const outfit = Outfit({
  subsets: ['latin'],
  weight: ['400', '700'],
})

function HomePage() {
  
  return (
   
    <div className="container">
      <main className = {outfit.className}>
      <header>
        <h1 className={outfit.className}>Welcome to Cityhacks</h1>
      </header>
        <div className="login-buttons">
          <Link href="/api/auth/login">
            <button>Student Login</button>
          </Link>
          <Link href="/api/auth/login">
            <button style={{padding: '20px 59px'}}>Tutor Login</button>
          </Link>
        </div>
        <p>New user?</p>
        <a href="/dashboard" style={{ fontSize: '1.5em' }}>See Demo</a>

       
      </main>
      <footer>
        {/* Footer content */}
      </footer>
    </div>
  );
}
// <a href="/api/auth/login">Login</a>
export default HomePage;

