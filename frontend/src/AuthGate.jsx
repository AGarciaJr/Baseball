import React, { useState } from 'react';
import Login from './Login.jsx';
import CreateAccount from './CreateAccount.jsx';

function getCookie(name) {
  const m = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return m ? m[2] : null;
}

export default function AuthGate() {
  const user = getCookie('user');
  const setFlag = getCookie('setFlag');
  const [mode, setMode] = useState('login'); 

  return mode === 'login' ? (
    <Login onSwitch={() => setMode('signup')} />
  ) : (
    <CreateAccount onSwitch={() => setMode('login')} />
  );
}