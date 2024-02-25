import React, { useEffect, useState } from "react";

export default function Plot( { districtName } ) {
    const [imageSrc, setImageSrc] = useState(null);
    const [imageLoadError, setImageLoadError] = useState(false);

    useEffect(() => {
        fetch("http://127.0.0.1:5000/plot.png", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify( { districtName: districtName.toUpperCase() }),
        })
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
    }, [districtName]);

    return (
        <div>
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