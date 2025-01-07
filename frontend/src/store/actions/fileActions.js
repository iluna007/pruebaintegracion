import { UPLOAD_FILE, FETCH_FILES } from "./types";

export const uploadFile = (file) => ({
	type: UPLOAD_FILE,
	payload: file,
});

export const fetchFiles = (filters) => ({
	type: FETCH_FILES,
	payload: filters, // Filtros como etiquetas, fechas, etc.
});
