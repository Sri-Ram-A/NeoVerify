
import React, { useState, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Image, Upload as UploadIcon, Trash2, FileImage, FileVideo, FileAudio, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

type FileType = "image" | "video" | "audio";

interface UploadFile {
  file: File;
  preview: string;
  type: FileType;
}

interface UploadProps {
  onFilesProcessed?: (files: Record<FileType, string | null>) => void;
}

const Upload: React.FC<UploadProps> = ({ onFilesProcessed }) => {
  const [files, setFiles] = useState<Record<FileType, UploadFile | null>>({
    image: null,
    video: null,
    audio: null,
  });
  const [activeTab, setActiveTab] = useState<FileType>("image");
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const getAcceptedFileTypes = (type: FileType) => {
    switch (type) {
      case "image":
        return "image/jpeg,image/png,image/gif";
      case "video":
        return "video/mp4,video/webm,video/quicktime";
      case "audio":
        return "audio/mpeg,audio/wav,audio/ogg";
      default:
        return "";
    }
  };

  const getSupportedFormats = (type: FileType) => {
    switch (type) {
      case "image":
        return "Supported formats: JPG, PNG, GIF";
      case "video":
        return "Supported formats: MP4, WEBM, MOV";
      case "audio":
        return "Supported formats: MP3, WAV, OGG";
      default:
        return "";
    }
  };

  const validateFile = (file: File, type: FileType): boolean => {
    const acceptedTypes = getAcceptedFileTypes(type).split(",");
    if (!acceptedTypes.includes(file.type)) {
      toast({
        title: "Invalid file type",
        description: `Please upload a valid ${type} file. ${getSupportedFormats(type)}`,
        variant: "destructive",
      });
      return false;
    }
    
    // 50MB limit
    if (file.size > 50 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "File size cannot exceed 50MB",
        variant: "destructive",
      });
      return false;
    }
    
    return true;
  };

  const handleFileChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      if (validateFile(file, activeTab)) {
        const reader = new FileReader();
        reader.onload = () => {
          setFiles((prev) => ({
            ...prev,
            [activeTab]: {
              file,
              preview: reader.result as string,
              type: activeTab,
            },
          }));
        };
        reader.readAsDataURL(file);
      }
      
      // Reset the input value to allow uploading the same file again
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    },
    [activeTab]
  );

  const handleDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setIsDragging(false);
      
      const file = event.dataTransfer.files[0];
      if (!file) return;
      
      if (validateFile(file, activeTab)) {
        const reader = new FileReader();
        reader.onload = () => {
          setFiles((prev) => ({
            ...prev,
            [activeTab]: {
              file,
              preview: reader.result as string,
              type: activeTab,
            },
          }));
        };
        reader.readAsDataURL(file);
      }
    },
    [activeTab]
  );

  const handleRemoveFile = useCallback((type: FileType) => {
    setFiles((prev) => ({
      ...prev,
      [type]: null,
    }));
  }, []);

  const handleButtonClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleProcess = useCallback(() => {
    const result: Record<FileType, string | null> = {
      image: files.image?.file.name || null,
      video: files.video?.file.name || null,
      audio: files.audio?.file.name || null,
    };
    
    if (onFilesProcessed) {
      onFilesProcessed(result);
    }
    
    toast({
      title: "Files processed successfully",
      description: "Your files have been processed.",
    });
    
    console.log(result);
  }, [files, onFilesProcessed]);

  const renderTabContent = () => {
    const currentFile = files[activeTab];
    
    if (currentFile) {
      return (
        <div className="relative rounded-lg overflow-hidden bg-gray-200 w-full">
          {activeTab === "image" && (
            <img
              src={currentFile.preview}
              alt="Preview"
              className="w-full h-64 object-contain"
            />
          )}
          {activeTab === "video" && (
            <video
              src={currentFile.preview}
              controls
              className="w-full h-64 object-contain"
            />
          )}
          {activeTab === "audio" && (
            <div className="w-full h-64 flex items-center justify-center bg-gray-100 p-4">
              <audio src={currentFile.preview} controls className="w-full" />
              <p className="text-gray-500 mt-2 text-sm">
                {currentFile.file.name}
              </p>
            </div>
          )}
          <div className="absolute top-2 right-2 flex space-x-2">
            <button
              onClick={() => handleRemoveFile(activeTab)}
              className="p-2 bg-red-500 rounded-full text-white hover:bg-red-600 transition-colors"
              aria-label="Delete file"
            >
              <Trash2 size={16} />
            </button>
          </div>
          <div className="p-2 flex items-center">
            <span className="text-sm text-gray-700 truncate flex-1">
              {currentFile.file.name}
            </span>
            <button
              onClick={() => handleRemoveFile(activeTab)}
              className="text-gray-400 hover:text-gray-700"
              aria-label="Close"
            >
              ×
            </button>
          </div>
        </div>
      );
    }

    return (
      <div
        className={`border-2 border-dashed rounded-lg p-12 flex flex-col items-center justify-center cursor-pointer transition-colors ${
          isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300"
        }`}
        onClick={handleButtonClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {activeTab === "image" && <FileImage size={36} className="text-gray-400 mb-4" />}
        {activeTab === "video" && <FileVideo size={36} className="text-gray-400 mb-4" />}
        {activeTab === "audio" && <FileAudio size={36} className="text-gray-400 mb-4" />}
        <p className="text-sm font-medium">Click to select</p>
        <p className="text-xs text-gray-500 mt-1">or drag and drop file here</p>
      </div>
    );
  };

  return (
    <div className="w-full max-w-md mx-auto bg-white rounded-lg shadow-sm border p-6">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-xl font-semibold">
          {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Upload
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab("image")}
            className={`p-2 rounded-md ${
              activeTab === "image" ? "bg-blue-100 text-blue-600" : "text-gray-500"
            }`}
          >
            <FileImage size={20} />
          </button>
          <button
            onClick={() => setActiveTab("video")}
            className={`p-2 rounded-md ${
              activeTab === "video" ? "bg-blue-100 text-blue-600" : "text-gray-500"
            }`}
          >
            <FileVideo size={20} />
          </button>
          <button
            onClick={() => setActiveTab("audio")}
            className={`p-2 rounded-md ${
              activeTab === "audio" ? "bg-blue-100 text-blue-600" : "text-gray-500"
            }`}
          >
            <FileAudio size={20} />
          </button>
        </div>
      </div>
      <p className="text-sm text-gray-500 mb-4">{getSupportedFormats(activeTab)}</p>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept={getAcceptedFileTypes(activeTab)}
      />

      {renderTabContent()}

      <div className="mt-6">
        <Button 
          onClick={handleProcess}
          className="w-full"
        >
          <Check className="mr-2 h-4 w-4" /> Process
        </Button>
      </div>
    </div>
  );
};

export default Upload;
