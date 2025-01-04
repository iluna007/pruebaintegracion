//import { useState } from 'react'
import React, { useState, useEffect } from "react";

import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { pingBackend } from "./api";   // Asegúrate de haber creado el archivo api.js


function App() {
  const [count, setCount] = useState(0)
  const [message, setMessage] = useState(""); // Nuevo estado para el mensaje

  useEffect(() => {
    const fetchData = async () => {
      const result = await pingBackend();
      if (result.error) {
        setMessage("Failed to connect to backend: " + result.error);
      } else {
        setMessage(result.message);
      }
    };

    fetchData();
  }, []);


  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React </h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
      {/* Nuevo componente para mostrar el mensaje */}
      <div className="backend-message">
        <h2>Backend Connection Test</h2>
        <p>{message}</p>
      </div>
    </>
  )
}

export default App
