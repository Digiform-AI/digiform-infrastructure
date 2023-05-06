import React, { useState } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import Printer from 'react-native-print';

const PrintScreen = () => {
  const [availablePrinters, setAvailablePrinters] = useState([]);

  const handlePrintPress = async () => {
    const printers = await Printer.selectPrinter();
    setAvailablePrinters(printers);
  };

  
  return (
    <View>
      <TouchableOpacity onPress={handlePrintPress}>
        <Text>Select Printer</Text>
      </TouchableOpacity>
      {availablePrinters.map(printer => (
        <Text key={printer.name}>{printer.name}</Text>
      ))}
    </View>
  );
};

export default PrintScreen;
