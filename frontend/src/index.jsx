import React from 'react';
import { createRoot } from 'react-dom/client';
import AuthGate from './AuthGate.jsx';
import './styles.css';
import { BrowserRouter } from 'react-router-dom';

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? match[2] : null;
}

const container = document.getElementById('root');
const root = createRoot(container);
const user = getCookie('user');

root.render(  <BrowserRouter>
  <AuthGate />
</BrowserRouter>);