"use client"
import React, { useState } from "react";
import Upload from "@/components/Upload";
import { Card } from "@/components/ui/card";

type FileType = "image" | "video" | "audio";

const Index = () => {
  const [processedFiles, setProcessedFiles] = useState<Record<FileType, string | null> | null>(null);

  const handleFilesProcessed = (files: Record<FileType, string | null>) => {
    setProcessedFiles(files);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold mb-8">File Flow Preview Process</h1>
      
      <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <Upload onFilesProcessed={handleFilesProcessed} />
        </div>
        
        {processedFiles && (
          <div>
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Processed Files</h2>
              <div className="bg-gray-100 p-4 rounded-md">
                <pre className="text-sm overflow-auto whitespace-pre-wrap">
                  {JSON.stringify(processedFiles, null, 2)}
                </pre>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default Index;
