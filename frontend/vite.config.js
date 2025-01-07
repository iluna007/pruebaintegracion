import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
	plugins: [react()],
	server: {
		port: 5173,
		host: true,
		hmr: {
			overlay: false, // Opcional: deshabilita superposición de errores
		},
	},
	resolve: {
		alias: {
			// Alias para Bootstrap en node_modules
			bootstrap: "/node_modules/bootstrap",
		},
	},
});
