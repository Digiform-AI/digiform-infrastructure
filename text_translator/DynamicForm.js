/*

import React, { useState } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Document, Page, Text as PdfText, StyleSheet, PDFViewer } from '@react-pdf/renderer';
import Printer from 'react-native-print';

const DynamicForm = () => {
  const [pdfDocument, setPdfDocument] = useState(null);

  const handlePrintPress = async () => {
    // Generate the PDF document
    const doc = (
      <Document>
        <Page style={styles.page}>
          <PdfText>Dynamic Form Content Goes Here</PdfText>
        </Page>
      </Document>
    );

    // Convert the document to a PDF file
    const pdfBlob = await doc.toBlob();
    const pdfUrl = URL.createObjectURL(pdfBlob);

    // Save the PDF file to state
    setPdfDocument(pdfUrl);

    // Select a printer and print the PDF document
    const printer = await Printer.selectPrinter();
    await Printer.print({ filePath: pdfUrl, printerUrl: printer.url });
  };

  return (
    <View>
      <TouchableOpacity onPress={handlePrintPress}>
        <Text>Print Form</Text>
      </TouchableOpacity>
      {pdfDocument && (
        <PDFViewer style={styles.pdfViewer} src={pdfDocument} />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#E4E4E4',
    padding: 10,
  },
  pdfViewer: {
    flex: 1,
  },
});

export default DynamicForm;


*/











import React, { useState } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import PDFView from 'react-native-pdf';
import * as Print from 'expo-print';

const DynamicForm = () => {
  const [pdfDocument, setPdfDocument] = useState(null);

  const handlePrintPress = async () => {
    // Generate the PDF document
    const htmlContent = '<h1>Dynamic Form Content Goes Here</h1>';

    // Convert the HTML content to a PDF file
    const pdfBlob = await Print.printToFileAsync({
      html: htmlContent,
      width: 612, // 8.5 inches in points
      height: 792, // 11 inches in points
      base64: false,
    });
    const pdfUrl = pdfBlob.uri;

    // Save the PDF file to state
    setPdfDocument(pdfUrl);

    // Select a printer and print the PDF document
    const printer = await Print.selectPrinterAsync();
    await Print.printAsync({ uri: pdfUrl, printerUrl: printer.url });
  };

  return (
    <View>
      <TouchableOpacity onPress={handlePrintPress}>
        <Text>Print Form</Text>
      </TouchableOpacity>
      {pdfDocument && (
        <PDFView style={styles.pdfViewer} source={{ uri: pdfDocument }} />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  pdfViewer: {
    flex: 1,
  },
});

export default DynamicForm;
