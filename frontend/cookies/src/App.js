import React, { useEffect } from 'react';
import axios from 'axios';

function App() {
  useEffect(() => {
    axios.get('http://127.0.0.1:5000/test')
      .then(response => {
        console.log(response.data);
      })
      .catch(error => {
        console.error('Il y a eu une erreur!', error);
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        {/* Votre contenu */}
      </header>
    </div>
  );
}

export default App;
