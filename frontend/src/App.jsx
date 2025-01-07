

import React from "react";

import "/node_modules/bootstrap/dist/css/bootstrap.min.css";

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Header from "./components/Header";
import Home from "./pages/Home";
import About from "./pages/About";
import RT from "./pages/ReactTest";


function App() {
	return (
		
		<Router>
			<Header />
			<Routes>
				<Route path='/' element={<Home />} />
				<Route path='/about' element={<About />} />
				<Route path='/reacttest' element={<RT />} />

			</Routes>
		</Router>
	);
}

export default App;
