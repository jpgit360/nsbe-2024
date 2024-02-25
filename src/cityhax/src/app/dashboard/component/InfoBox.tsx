import React, { useEffect, useState } from "react";

export default function InfoBox({ districtName }) {
    const [jsonData, setJsonData] = useState(null);
    const [dataLoadError, setDataLoadError] = useState(false);

    useEffect(() => {
        fetch("http://127.0.0.1:5000/api/districts", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ districtName: districtName.toUpperCase() }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Data fetch failed with status: " + response.status);
                }
                return response.json();
            })
            .then((data) => {
                setJsonData(data);
            })
            .catch((error) => {
                console.error("Error fetching data:", error);
                setDataLoadError(true);
            });
    }, [districtName]);

    return (
        <div>
            {jsonData ? (
                <pre className="json-text">
                    {Object.entries(jsonData).map(([key, value]) => (
                        <div key={key}>
                            <span className="font-semibold">{key}:</span> {value}
                        </div>
                    ))}
                </pre>
            ) : dataLoadError ? (
                <p>Error loading data.</p>
            ) : (
                <p>Loading data...</p>
            )}
        </div>
    );
}
