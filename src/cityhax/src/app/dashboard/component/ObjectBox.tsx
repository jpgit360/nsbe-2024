import React, { useState, useEffect } from "react";

function ObjectBox({ jsonData }) {
    return (
      <div className="box">
        <span className="name">{jsonData.nickname}<br/>{jsonData.email}
        <br/>{jsonData.university} <br/> {jsonData.ACT} 
        <br/> {jsonData.SAT}<br/> {jsonData.MAJOR} </span>
      </div>
    );
  }

export default function Box() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/data") // Replace with your actual endpoint
      .then((response) => response.json())
      .then((data) => {
        // Ensure backend data aligns with expected format
        const formattedData = data.map((user) => ({
            nickname: user.nickname,
            email: user.email,
            university: "MIT",
            ACT: "35",
            MAJOR: "CS/ENG",
            SAT: "1600"
        }));
        setData(formattedData);
      });
  }, []);

  const renderBoxes = () => {
    return (
      <div className="box"> 
        {data.map((obj, index) => (
          <ObjectBox key={obj.id} jsonData={obj} />
        ))}
      </div>
    );
  };

  return (
    <div className="grid-container">
      {renderBoxes()}
    </div>
  );
}
