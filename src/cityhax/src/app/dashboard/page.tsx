"use client";
import React, { use, useEffect, useState } from "react";
import SearchBar from "./component/searchbar"
import axios from "axios";

import { Outfit } from 'next/font/google';
const outfit = Outfit({
  subsets: ['latin'],
  weight: ['400', '700'],
})

export default function DashBoad() {
  const [imageSrc, setImageSrc] = useState(null);
  const [imageLoadError, setImageLoadError] = useState(false);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/plot.png")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Image fetch failed with status: " + response.status);
        }
        return response.blob();
      })
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        setImageSrc(url);
      })
      .catch((error) => {
        console.error("Error fetching image:", error);
        setImageLoadError(true);
      });
  }, []);

  return (
    <div className={outfit.className}>
      <p className="welcome-text">Welcome User</p>
      <SearchBar />
      {imageSrc ? (
        <img src={imageSrc} alt="Generated Plot" />
      ) : imageLoadError ? (
        <p>Error loading image.</p>
      ) : (
        <p>Loading image...</p>
      )}
    </div>
  );
}