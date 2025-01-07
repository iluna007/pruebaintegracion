// Punto de entrada para los stores y contexto
import rootStore from "./stores/rootStore";
import { createContext, useContext } from "react";

const StoreContext = createContext(rootStore);

export const StoreProvider = ({ children }) => (
	<StoreContext.Provider value={rootStore}>{children}</StoreContext.Provider>
);

export const useStores = () => useContext(StoreContext);
