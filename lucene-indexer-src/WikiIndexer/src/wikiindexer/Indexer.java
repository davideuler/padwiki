/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package wikiindexer;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.WhitespaceAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.store.FSDirectory;

/**
 *
 * @author euler
 */
public class Indexer {

    private static final File INDEX_DIR = new File("db.lucene");
    private static final Analyzer ANALYZER = new WhitespaceAnalyzer();
    private static final int MAX_FIELD_LENGTH = 65536;
    private static final int MAX_KEY = 230;

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        IndexWriter writer;
        BufferedReader bufReader;
        try {

            if (INDEX_DIR.exists()) {
                writer = new IndexWriter(FSDirectory.open(INDEX_DIR), ANALYZER, false,
                        new IndexWriter.MaxFieldLength(MAX_FIELD_LENGTH));
            } else {
                writer = new IndexWriter(FSDirectory.open(INDEX_DIR), ANALYZER, true,
                        new IndexWriter.MaxFieldLength(MAX_FIELD_LENGTH));
            }

            if (null == writer) {
                System.err.println("error create/opening index");
                return;
            }
            bufReader = new BufferedReader(new InputStreamReader(System.in));

            if (null == bufReader) {
                System.err.println("error reading system input");
                return;
            }

            writer.setRAMBufferSizeMB(512);

            //docId : the the filename of rec00xxxyy-YYYYMMDD-pages-articles.xml.bz2
            String docId = "";

            String title;
            long total = 0;

            while ((title = bufReader.readLine()) != null) {
                int l = title.length();

                try {

                    if (l > 4 && title.charAt(0) == '#' && title.substring(l - 4).equals(".bz2")) {
                        docId = title.substring(1);

                        continue;
                    }

                    if (l == 0) {
                        continue;
                    }

                    //cerr << title.c_str() << endl;
                    String Title = title;
                    title = title.toLowerCase();

                    //make the document:
                    Document newdocument = new Document();

                    // Target: filename and the exact title used
                    String target = docId + ":" + Title;
                    if (target.length() > MAX_KEY) {
                        target = target.substring(0, MAX_KEY);
                    }

                    // data: for showing in the search result, search result as following format:
                    // 67% [rec00028enwiktionary-20080315-pages-articles.xml.bz2:free speech]
                    newdocument.add(new Field("data", target, Field.Store.YES, Field.Index.NO));

                    // 1st Source: the lowercased title; to add search term to document.
                    if (title.length() > MAX_KEY) {
                        title = title.substring(0, MAX_KEY);
                    }

                    //commented by David Lv, 2010/02/28, for exact title query(to display article)
                    newdocument.add(new Field("title", title, Field.Store.NO, Field.Index.NOT_ANALYZED_NO_NORMS));

                    // 2nd source: All the title's lowercased words
                    newdocument.add(new Field("title", title, Field.Store.NO, Field.Index.ANALYZED));

                    try {
                        writer.addDocument(newdocument);
                    } catch (IOException ioe) {
                        System.out.println("Exception:" + ioe.getMessage());
                        System.out.println("When adding:\n" + title);
                        System.out.println("Of Length " + title.length());
                    }

                    total++;

                    if ((total % 81920) == 0) {
                        System.out.println(total + " articles indexed so far");
                    }
                } catch (Exception ex) {
                    ex.printStackTrace();
                    System.out.println("Exception: " + ex.getMessage());
                    System.err.println("title:" + title );
                }
            } // end of while

            writer.optimize();
            writer.close();
            
            System.out.println(total + " articles indexed.");

        } catch (IOException ex) {
            Logger.getLogger(Indexer.class.getName()).log(Level.SEVERE, null, ex);
        }

    }
}
