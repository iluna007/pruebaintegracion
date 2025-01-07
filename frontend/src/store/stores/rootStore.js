// Agrupa todos los stores para facilitar su acceso
import userStore from "./userStore";
import fileStore from "./fileStore";

const rootStore = {
	userStore,
	fileStore,
};

export default rootStore;
