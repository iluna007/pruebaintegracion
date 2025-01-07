import React from "react";
import "./home.css";

export const Home = () => {
	return (
			<div className='p-5 mb-4 bg-light rounded-0'>
				<div className='container-fluid py-5 text-start'>
					<h1 className='display-5 fw-bold'>Hello, world!</h1>
					<p className='col-md-8 fs-4'>
						This is a simple hero unit, a simple jumbotron-style component for
						calling extra attention to featured content or information.
					</p>
					<hr className='my-4' />
					<p>It uses Vite + React + Flask + Python + PostgreSQL + Bootstrap.</p>
					<a className='btn btn-primary btn-lg' href='#' role='button'>
						Learn more
					</a>
				</div>
			</div>
	);
};

export default Home;