export const pingBackend = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/ping");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error connecting to backend:", error);
      return { error: error.message };
    }
  };
  