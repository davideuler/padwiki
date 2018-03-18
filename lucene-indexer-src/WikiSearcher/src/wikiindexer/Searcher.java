/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package wikiindexer;

import java.io.File;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.Term;
import org.apache.lucene.search.BooleanClause.Occur;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.FSDirectory;

/**
 *
 * @author euler
 */
public class Searcher {

//    private static final Analyzer ANALYZER = new StandardAnalyzer(Version.LUCENE_30);
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {

        // Simplest possible options parsing: 1st param the index path, 2nd param the query keyword
        //System.out.println("args[0]:" + args[0]);

        if (args.length < 2) {
            System.out.println("usage: java -jar WikiSearcher.jar <path to database> <search terms>");
            System.exit(-1);
        }
        String dbPath = args[0];

        IndexSearcher searcher;
        File indexDir = new File(dbPath);

        try {
            if (!indexDir.exists()) {
                System.err.println("index does not exist!");
                return;
            }

            searcher = new IndexSearcher(FSDirectory.open(indexDir), true);

            if (null == searcher) {
                System.err.println("error reading index");
                return;
            }
            //System.out.println("searching...");
//            QueryParser parser = new QueryParser(Version.LUCENE_30 ,"title", ANALYZER);
//            parser.setDefaultOperator(QueryParser.Operator.AND);
//            Query query = parser.parse(keyword);

            BooleanQuery query = new BooleanQuery();

            for (int i = 1; i < args.length; i++) {
                String keyword = args[i];
                TermQuery termQuery = new TermQuery(new Term("title", keyword));
                query.add(termQuery,Occur.MUST);
                //System.out.println("term:" + keyword);
            }

            TopDocs search = searcher.search(query, 50);

            for (int i = 0; i < search.scoreDocs.length; i++) {
                ScoreDoc scoreDoc = search.scoreDocs[i];
                Document doc = searcher.doc(scoreDoc.doc);
                Float score = scoreDoc.score;

                System.out.println(score.intValue() + " [" + doc.get("data") + "]");

            }

        } catch (IOException ex) {
            Logger.getLogger(Searcher.class.getName()).log(Level.SEVERE, null, ex);
        }

    }
}
