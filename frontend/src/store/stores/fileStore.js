// Maneja el estado relacionado con los archivos subidos
import { UPLOAD_FILE, FETCH_FILES } from "../actions/types";

let files = [];

const fileStore = {
	getFiles: () => files,

	dispatch: (action) => {
		switch (action.type) {
			case UPLOAD_FILE:
				files.push(action.payload);
				break;
			case FETCH_FILES:
				files = files.filter((file) =>
					Object.entries(action.payload).every(
						([key, value]) => file[key] === value
					)
				);
				break;
			default:
				console.error("Acción no reconocida:", action.type);
		}
	},
};

export default fileStore;
