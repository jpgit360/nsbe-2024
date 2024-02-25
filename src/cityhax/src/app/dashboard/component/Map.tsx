import React, { useEffect, useState } from "react";
import Plot from 'react-plotly.js';

export default function Map() {
    const [plot, setPlot] = useState(0);
      
    useEffect(() => {
      fetch('http://127.0.0.1:5000/map')
        .then(res => res.json())
        .then(data => {
          if (Object.keys(data).length !== 0) {
            setPlot(data);
          } else {
            console.warn('Fetched JSON data is empty.');
          }
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
    }, []);
    
    return (
        <div>
            <Plot data={plot.data} layout={plot.layout}/>
        </div>
    );
  }