import React, { useRef } from 'react';
import ConfigPage from './pages/ConfigPage';
import CrawlerStatusPage from './pages/CrawlerStatusPage';

export default function App() {
  const configPageRef = useRef();

  return (
    <div style={{maxWidth:600,margin:'0 auto',padding:24}}>
      <h1>MediaCrawler 可视化配置与进程管理</h1>
      <ConfigPage ref={configPageRef} />
      <div id="crawler-status">
        <CrawlerStatusPage />
      </div>
    </div>
  );
} 