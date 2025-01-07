// Maneja el estado relacionado con los usuarios
import { REGISTER_USER, LOGIN_USER } from "../actions/types";

let currentUser = null;

const userStore = {
	getCurrentUser: () => currentUser,

	dispatch: (action) => {
		switch (action.type) {
			case REGISTER_USER:
				currentUser = action.payload;
				break;
			case LOGIN_USER:
				currentUser = { id: 1, username: action.payload.username };
				break;
			default:
				console.error("Acción no reconocida:", action.type);
		}
	},
};

export default userStore;
