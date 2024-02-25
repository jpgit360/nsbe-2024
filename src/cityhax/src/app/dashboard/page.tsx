"use client";
import {useState} from "react";
import SearchBar from "./component/searchbar"

import { Outfit } from 'next/font/google';
const outfit = Outfit({
  subsets: ['latin'],
  weight: ['400', '700'],
})

export default function DashBoad() {
   
 return (
    <div className = {outfit.className}>
       <p className="welcome-text">Welcome User</p>
    
      <SearchBar />

      {/* Rest of your content */}
    </div>
  );
}