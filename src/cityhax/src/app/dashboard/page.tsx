"use client";
import React from "react";
import SearchBar from "./component/searchbar"
import Map from "./component/Map"
import Plot from "./component/Plot"
import InfoBox from "./component/InfoBox";

import { Outfit } from 'next/font/google';
const outfit = Outfit({
  subsets: ['latin'],
  weight: ['400', '700'],
})

export default function DashBoad() {
  return (
    <div className={outfit.className}>
      <p className="welcome-text">Welcome User</p>
      <SearchBar />
      <InfoBox districtName={"HUMPHREYS CO SCHOOL DIST"} />
    </div>
  );
}