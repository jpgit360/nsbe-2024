"use client";
import React, { useState } from "react";
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
  const [searchTerm, setSearchTerm] = useState<string>('');

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    // You can perform any actions with the search term here
  };

  return (
    <div className={outfit.className}>
      <p className="welcome-text">Welcome User</p>
      <SearchBar onSearch={handleSearch} />
      <div className="plot-map-container">
        {/* Plot and Map side by side */}
        <div className="plot">
          <Plot districtName={searchTerm.toUpperCase()} />
        </div>
        <div className="map">
          <Map />
        </div>
      </div>
      <div className="info-box">
        {/* Info Box centered below */}
        <InfoBox districtName={searchTerm.toUpperCase()} />
      </div>
    </div>
  );
}