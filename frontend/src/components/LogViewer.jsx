import React from 'react';

export default function LogViewer({ logs }) {
  return (
    <pre style={{maxHeight:300,overflow:'auto',background:'#222',color:'#fff',padding:8}}>
      {logs.join('')}
    </pre>
  );
} 