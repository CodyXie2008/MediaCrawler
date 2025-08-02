import React, { useEffect, useState } from 'react';
import { getStatus, getLogs, stopCrawler } from '../api/index';
import CrawlerStatus from '../components/CrawlerStatus';
import LogViewer from '../components/LogViewer';

export default function CrawlerStatusPage() {
  const [status, setStatus] = useState({});
  const [logs, setLogs] = useState([]);
  useEffect(() => {
    const timer = setInterval(() => {
      getStatus().then(setStatus);
      getLogs().then(res => setLogs(res.logs || []));
    }, 2000);
    return () => clearInterval(timer);
  }, []);
  return (
    <div>
      <CrawlerStatus status={status} onStop={stopCrawler} />
      <LogViewer logs={logs} />
    </div>
  );
} 