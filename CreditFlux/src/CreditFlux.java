
import java.awt.Desktop;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Scanner;

public class CreditFlux {
	public void open(String targetFilePath) throws IOException
	 {
	     Desktop desktop = Desktop.getDesktop();
	     desktop.open(new File(targetFilePath));
	 }
	
    public static void main(String[] args) throws IOException {
    	Scanner scan = new Scanner(System.in);
    	System.out.println("Open main.exe to download? (Yes or no)");
    	String manual_download = scan.nextLine();
    	
    	if(manual_download.equalsIgnoreCase("yes")) {
    		CreditFlux cf = new CreditFlux();
    		//need to change to your local path of main.exe
    		String targetFilePath = "C:\\Users\\znan3\\OneDrive\\Documents\\creditflux_downloader\\main.exe";
    		cf.open(targetFilePath);
    	}else {
    		Process proc;
            try {
            	System.out.println("Single deal?(Yes or no):");
            	String single_multi = scan.nextLine();
            	String deal;
            	if(single_multi.equalsIgnoreCase("yes")) {
            		System.out.println("Give the name for the deal: ");
            		deal = scan.nextLine();
            	}else {
            		System.out.println("Give the filepath for the deal: ");
            		deal = scan.nextLine();
            	}
            	
            	//need to change to your local path of main2.py
            	String main_py = "C:\\Users\\znan3\\OneDrive\\Documents\\creditflux_downloader\\main2.py";
            	
            	String[] str=new String[]{"python", main_py, single_multi, deal};
                proc = Runtime.getRuntime().exec(str);
                System.out.print("Starting...");
                BufferedReader in = new BufferedReader(new InputStreamReader(proc.getInputStream()));
                String line = null;
                while ((line = in.readLine()) != null) {
                    System.out.println(line);
                }
                in.close();
                System.out.println("end");
                proc.waitFor();
            } catch (IOException e) {
                e.printStackTrace();
            } catch (InterruptedException e) {
                e.printStackTrace();
            } 
        }
    	}
}