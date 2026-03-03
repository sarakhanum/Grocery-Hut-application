import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

import { Provider } from 'react-redux';
import store from './store';

import { BrowserRouter } from "react-router-dom";   // ✅ ADD THIS

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>          {/* ✅ ADD THIS */}
        <App />
      </BrowserRouter>         {/* ✅ ADD THIS */}
    </Provider>
  </React.StrictMode>
);

reportWebVitals();
