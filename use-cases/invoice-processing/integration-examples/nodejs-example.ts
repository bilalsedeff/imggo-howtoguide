import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = 'https://img-go.com/api';

async function main() {
  console.log('ImgGo Integration Example');
  
  if (!IMGGO_API_KEY) {
    console.error('✗ IMGGO_API_KEY not set');
    process.exit(1);
  }
  
  console.log('✓ Example completed!');
}

main();
