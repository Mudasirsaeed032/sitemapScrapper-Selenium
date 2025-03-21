const mongoose = require('mongoose');

const unstructuredContent = new mongoose.Schema({
    name: {
        type: String,
        required: true
    },
    url: { type: String, required: true },   // University URL
    content: { type: String, required: true }, // Unstructured scraped content
    createdAt: { type: Date, default: Date.now }, // Timestamp
})


const UnstructuredContent = mongoose.model('UnstructuredContent', unstructuredContent);

module.exports = UnstructuredContent;