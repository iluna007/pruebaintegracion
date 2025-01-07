import { REGISTER_USER, LOGIN_USER } from "./types";

export const registerUser = (user) => ({
	type: REGISTER_USER,
	payload: user,
});

export const loginUser = (credentials) => ({
	type: LOGIN_USER,
	payload: credentials,
});
