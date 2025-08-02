import React from 'react';
import { Progress, Button } from 'antd';

export default function CrawlerStatus({ status, onStop }) {
  return (
    <div>
      <div>状态：{status.running ? '运行中' : '已停止'}</div>
      <Progress percent={status.progress || 0} />
      <Button onClick={onStop} disabled={!status.running}>停止爬虫</Button>
    </div>
  );
} 