import React, { useEffect, useState } from "react";

export default function Users() {
    useEffect(() => {
        fetch('http://127.0.0.1:5000/data')
          .then(res => res.json())
          .then(data => {
            if (Object.keys(data).length !== 0) {
              console.log(data)
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
            
        </div>
    );

}