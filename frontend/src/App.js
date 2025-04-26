import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  TextField, 
  Button, 
  Paper, 
  Typography,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

// Configure axios defaults
axios.defaults.baseURL = API_URL;
axios.defaults.headers.common['Content-Type'] = 'application/json';

const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

function App() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  // Test backend connection on component mount
  useEffect(() => {
    const testConnection = async () => {
      try {
        console.log('Testing backend connection to:', API_URL);
        const response = await axios.get('/test', {
          timeout: 5000, // 5 second timeout
          validateStatus: function (status) {
            return status >= 200 && status < 500; // Accept any status code less than 500
          }
        });
        
        if (response.status === 200) {
          console.log('Backend connection test response:', response.data);
          setIsConnected(true);
          setMessages(prev => [...prev, {
            type: 'system',
            content: 'Connected to backend successfully'
          }]);
        } else {
          console.error('Backend returned non-200 status:', response.status);
          setMessages(prev => [...prev, {
            type: 'error',
            content: `Backend returned status ${response.status}. Please check if the backend server is running correctly.`
          }]);
        }
      } catch (error) {
        console.error('Backend connection test failed:', error);
        let errorMessage = 'Failed to connect to backend. ';
        
        if (error.code === 'ECONNREFUSED') {
          errorMessage += 'The backend server is not running or not accessible.';
        } else if (error.code === 'ETIMEDOUT') {
          errorMessage += 'Connection timed out. The backend server might be busy or not responding.';
        } else {
          errorMessage += `Error: ${error.message}`;
        }
        
        setMessages(prev => [...prev, {
          type: 'error',
          content: errorMessage
        }]);
      }
    };

    testConnection();
  }, []);

  const handleFileUpload = async (event) => {
    if (!isConnected) {
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Cannot upload file: Not connected to backend'
      }]);
      return;
    }

    const file = event.target.files[0];
    if (!file) {
      console.log('No file selected');
      return;
    }

    console.log('Starting file upload:', file.name);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('Sending file to backend...');
      const response = await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('Upload response:', response.data);
      
      setMessages(prev => [...prev, {
        type: 'system',
        content: `File "${file.name}" uploaded successfully`
      }]);
    } catch (error) {
      console.error('Upload error:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      setMessages(prev => [...prev, {
        type: 'error',
        content: `Error uploading file: ${error.response?.data?.detail || error.message}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isConnected) {
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Cannot send question: Not connected to backend'
      }]);
      return;
    }

    if (!question.trim()) {
      console.log('Empty question submitted');
      return;
    }

    console.log('Submitting question:', question);
    setLoading(true);
    setMessages(prev => [...prev, {
      type: 'user',
      content: question
    }]);

    try {
      console.log('Sending question to backend...');
      const response = await axios.post('/chat', {
        question: question
      });
      console.log('Chat response:', response.data);

      setMessages(prev => [...prev, {
        type: 'ai',
        content: response.data.answer,
        reasoning: response.data.reasoning
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      setMessages(prev => [...prev, {
        type: 'error',
        content: `Error getting response: ${error.response?.data?.detail || error.message}`
      }]);
    } finally {
      setLoading(false);
      setQuestion('');
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          AI Chat with RAG
        </Typography>

        <Paper elevation={3} sx={{ p: 2, mb: 2, height: '60vh', overflow: 'auto' }}>
          <List>
            {messages.map((message, index) => (
              <React.Fragment key={index}>
                <ListItem>
                  <ListItemText
                    primary={message.content}
                    secondary={message.reasoning}
                    sx={{
                      bgcolor: message.type === 'user' ? '#e3f2fd' : 
                              message.type === 'error' ? '#ffebee' : 
                              message.type === 'system' ? '#f5f5f5' : '#f1f8e9',
                      p: 2,
                      borderRadius: 1
                    }}
                  />
                </ListItem>
                {index < messages.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Paper>

        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 2 }}>
          <Button
            component="label"
            variant="contained"
            startIcon={<CloudUploadIcon />}
            disabled={loading}
          >
            Upload File
            <VisuallyHiddenInput type="file" onChange={handleFileUpload} accept=".txt,.pdf" />
          </Button>

          <TextField
            fullWidth
            variant="outlined"
            placeholder="Ask a question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={loading}
          />

          <Button
            type="submit"
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Send'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
}

export default App; 