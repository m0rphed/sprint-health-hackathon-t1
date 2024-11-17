"use client";

import { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { FileSpreadsheet, Upload, Folder, MoreVertical, Pencil, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { supabase } from "@/lib/supabase";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { SprintCharts } from "@/components/sprint-charts";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { cn, truncateFilename } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

interface UploadFolder {
  id: string;
  name: string;
  created_at: string;
}

interface SprintFile {
  name: string;
  created_at: string;
  metadata: {
    size: number;
  };
}

export default function DashboardPage() {
  const [uploadFolders, setUploadFolders] = useState<UploadFolder[]>([]);
  const [files, setFiles] = useState<SprintFile[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<UploadFolder | null>(null);
  const [selectedFile, setSelectedFile] = useState<SprintFile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRenameDialogOpen, setIsRenameDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const { toast } = useToast();

  const fetchUploadFolders = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase.storage
        .from('sprint-data')
        .list(user.id, {
          limit: 100,
          offset: 0,
          sortBy: { column: 'created_at', order: 'desc' }
        });

      if (error) throw error;

      // Filter only directories
      const folders = data
        .filter(item => !item.name.includes('.'))
        .map(folder => ({
          name: folder.name,
          id: folder.name,
          created_at: folder.created_at
        }));

      setUploadFolders(folders);
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
    }
  };

  const fetchFiles = async (folderId: string) => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase.storage
        .from('sprint-data')
        .list(`${user.id}/${folderId}`);

      if (error) throw error;

      // Filter only CSV files
      const csvFiles = data.filter(file => file.name.endsWith('.csv'));
      setFiles(csvFiles);
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
    }
  };

  useEffect(() => {
    fetchUploadFolders();
  }, []);

  useEffect(() => {
    if (selectedFolder) {
      fetchFiles(selectedFolder.id);
    } else {
      setFiles([]);
    }
  }, [selectedFolder]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    try {
      setIsLoading(true);
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const folderName = `upload-${Date.now()}`;
      const folderPath = `${user.id}/${folderName}`;

      // Upload all files to the new folder
      for (const file of acceptedFiles) {
        if (!file.name.endsWith('.csv')) {
          throw new Error("Only CSV files are allowed");
        }

        const { error } = await supabase.storage
          .from('sprint-data')
          .upload(`${folderPath}/${file.name}`, file);

        if (error) throw error;
      }

      toast({
        title: "Success",
        description: "Files uploaded successfully",
      });

      await fetchUploadFolders();
      setSelectedFolder({
        name: folderName,
        id: folderName,
        created_at: new Date().toISOString()
      });
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleRenameFolder = async () => {
    try {
      if (!selectedFolder) return;

      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // Move all files from old folder to new folder
      for (const file of files) {
        const oldPath = `${user.id}/${selectedFolder.id}/${file.name}`;
        const newPath = `${user.id}/${newFolderName}/${file.name}`;

        // Copy file to new location
        const { error: copyError } = await supabase.storage
          .from('sprint-data')
          .copy(oldPath, newPath);

        if (copyError) throw copyError;

        // Delete file from old location
        const { error: deleteError } = await supabase.storage
          .from('sprint-data')
          .remove([oldPath]);

        if (deleteError) throw deleteError;
      }

      toast({
        title: "Success",
        description: "Folder renamed successfully",
      });

      await fetchUploadFolders();
      setSelectedFolder(prev => prev ? {
        ...prev,
        name: newFolderName,
        id: newFolderName
      } : null);
      setIsRenameDialogOpen(false);
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
    }
  };

  const handleDeleteFolder = async () => {
    try {
      if (!selectedFolder) return;

      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const filePaths = files.map(file => 
        `${user.id}/${selectedFolder.id}/${file.name}`
      );

      const { error } = await supabase.storage
        .from('sprint-data')
        .remove(filePaths);

      if (error) throw error;

      toast({
        title: "Success",
        description: "Folder deleted successfully",
      });

      setSelectedFolder(null);
      setSelectedFile(null);
      fetchUploadFolders();
      setIsDeleteDialogOpen(false);
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
  });

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="w-64 border-r bg-card">
        <div className="p-4">
          <h2 className="text-lg font-semibold mb-4">Sprint Data</h2>
          <div {...getRootProps()} className={`
            border-2 border-dashed rounded-lg p-4 mb-4 transition-colors
            ${isDragActive ? 'border-primary bg-primary/10' : 'border-border'}
          `}>
            <input {...getInputProps()} />
            <div className="text-center">
              <Upload className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">
                {isDragActive ? "Drop files here" : "Drag & drop CSV files here"}
              </p>
              <Button
                variant="outline"
                size="sm"
                className="mt-2"
                disabled={isLoading}
              >
                {isLoading ? "Uploading..." : "Select Files"}
              </Button>
            </div>
          </div>
          <Separator className="my-4" />
          <div className="space-y-2">
            {uploadFolders.map((folder) => (
              <div
                key={folder.id}
                className="flex items-center justify-between group"
              >
                <Button
                  variant={selectedFolder?.id === folder.id ? "secondary" : "ghost"}
                  className="flex-1 justify-start"
                  onClick={() => {
                    setSelectedFolder(folder);
                    setSelectedFile(null);
                  }}
                >
                  <Folder className="mr-2 h-4 w-4" />
                  <span className="truncate">{folder.name}</span>
                </Button>
                {selectedFolder?.id === folder.id && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={() => {
                          setNewFolderName(folder.name);
                          setIsRenameDialogOpen(true);
                        }}
                      >
                        <Pencil className="mr-2 h-4 w-4" />
                        Rename
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="text-destructive"
                        onClick={() => setIsDeleteDialogOpen(true)}
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-6">
          {selectedFolder ? (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">{selectedFolder.name}</h1>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {files.map((file) => (
                  <Card
                    key={file.name}
                    className={`p-4 cursor-pointer transition-colors ${
                      selectedFile?.name === file.name ? 'border-primary' : ''
                    }`}
                    onClick={() => setSelectedFile(file)}
                  >
                    <div className="flex items-center space-x-3">
                      <FileSpreadsheet className="h-8 w-8 text-primary" />
                      <div>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <p className="font-medium">
                              {truncateFilename(file.name)}
                            </p>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>{file.name}</p>
                          </TooltipContent>
                        </Tooltip>
                        <p className="text-sm text-muted-foreground">
                          {new Date(file.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {selectedFile && (
                <Tabs defaultValue="overview" className="space-y-4">
                  <TabsList>
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="analysis">Analysis</TabsTrigger>
                  </TabsList>

                  <TabsContent value="overview">
                    <SprintCharts sprintId={selectedFile.name} />
                  </TabsContent>

                  <TabsContent value="analysis">
                    <Card className="p-6">
                      <h3 className="text-lg font-semibold mb-4">Detailed Analysis</h3>
                      <p className="text-muted-foreground">
                        Detailed sprint analysis coming soon...
                      </p>
                    </Card>
                  </TabsContent>
                </Tabs>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Folder className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h2 className="text-xl font-semibold mb-2">No Folder Selected</h2>
                <p className="text-muted-foreground">
                  Select a folder from the sidebar or upload new files to create one
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Rename Dialog */}
      <Dialog open={isRenameDialogOpen} onOpenChange={setIsRenameDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename Folder</DialogTitle>
          </DialogHeader>
          <Input
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            placeholder="Enter new folder name"
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsRenameDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleRenameFolder}>
              Rename
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the folder and all its contents.
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteFolder}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}